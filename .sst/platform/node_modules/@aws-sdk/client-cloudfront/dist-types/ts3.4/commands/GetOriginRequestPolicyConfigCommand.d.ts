import { EndpointParameterInstructions } from "@smithy/middleware-endpoint";
import { Command as $Command } from "@smithy/smithy-client";
import {
  Handler,
  HttpHandlerOptions as __HttpHandlerOptions,
  MetadataBearer as __MetadataBearer,
  MiddlewareStack,
} from "@smithy/types";
import {
  CloudFrontClientResolvedConfig,
  ServiceInputTypes,
  ServiceOutputTypes,
} from "../CloudFrontClient";
import {
  GetOriginRequestPolicyConfigRequest,
  GetOriginRequestPolicyConfigResult,
} from "../models/models_1";
export { __MetadataBearer, $Command };
export interface GetOriginRequestPolicyConfigCommandInput
  extends GetOriginRequestPolicyConfigRequest {}
export interface GetOriginRequestPolicyConfigCommandOutput
  extends GetOriginRequestPolicyConfigResult,
    __MetadataBearer {}
export declare class GetOriginRequestPolicyConfigCommand extends $Command<
  GetOriginRequestPolicyConfigCommandInput,
  GetOriginRequestPolicyConfigCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: GetOriginRequestPolicyConfigCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: GetOriginRequestPolicyConfigCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<
    GetOriginRequestPolicyConfigCommandInput,
    GetOriginRequestPolicyConfigCommandOutput
  >;
  private serialize;
  private deserialize;
}
