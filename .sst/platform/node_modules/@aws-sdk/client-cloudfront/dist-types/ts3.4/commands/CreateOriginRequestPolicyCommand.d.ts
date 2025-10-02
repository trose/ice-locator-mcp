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
  CreateOriginRequestPolicyRequest,
  CreateOriginRequestPolicyResult,
} from "../models/models_0";
export { __MetadataBearer, $Command };
export interface CreateOriginRequestPolicyCommandInput
  extends CreateOriginRequestPolicyRequest {}
export interface CreateOriginRequestPolicyCommandOutput
  extends CreateOriginRequestPolicyResult,
    __MetadataBearer {}
export declare class CreateOriginRequestPolicyCommand extends $Command<
  CreateOriginRequestPolicyCommandInput,
  CreateOriginRequestPolicyCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: CreateOriginRequestPolicyCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: CreateOriginRequestPolicyCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<
    CreateOriginRequestPolicyCommandInput,
    CreateOriginRequestPolicyCommandOutput
  >;
  private serialize;
  private deserialize;
}
