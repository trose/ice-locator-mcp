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
  GetOriginRequestPolicyRequest,
  GetOriginRequestPolicyResult,
} from "../models/models_1";
export { __MetadataBearer, $Command };
export interface GetOriginRequestPolicyCommandInput
  extends GetOriginRequestPolicyRequest {}
export interface GetOriginRequestPolicyCommandOutput
  extends GetOriginRequestPolicyResult,
    __MetadataBearer {}
export declare class GetOriginRequestPolicyCommand extends $Command<
  GetOriginRequestPolicyCommandInput,
  GetOriginRequestPolicyCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: GetOriginRequestPolicyCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: GetOriginRequestPolicyCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<
    GetOriginRequestPolicyCommandInput,
    GetOriginRequestPolicyCommandOutput
  >;
  private serialize;
  private deserialize;
}
