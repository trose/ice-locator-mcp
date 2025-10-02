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
  UpdateOriginRequestPolicyRequest,
  UpdateOriginRequestPolicyResult,
} from "../models/models_1";
export { __MetadataBearer, $Command };
export interface UpdateOriginRequestPolicyCommandInput
  extends UpdateOriginRequestPolicyRequest {}
export interface UpdateOriginRequestPolicyCommandOutput
  extends UpdateOriginRequestPolicyResult,
    __MetadataBearer {}
export declare class UpdateOriginRequestPolicyCommand extends $Command<
  UpdateOriginRequestPolicyCommandInput,
  UpdateOriginRequestPolicyCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: UpdateOriginRequestPolicyCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: UpdateOriginRequestPolicyCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<
    UpdateOriginRequestPolicyCommandInput,
    UpdateOriginRequestPolicyCommandOutput
  >;
  private serialize;
  private deserialize;
}
